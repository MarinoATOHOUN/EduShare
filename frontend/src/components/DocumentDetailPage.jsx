/**
 * Document Detail Page Component for PDF Course Sharing Platform
 * Developed by Marino ATOHOUN
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Download,
  Eye,
  Calendar,
  User,
  FileText,
  ArrowLeft,
  Share2,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { documentsAPI } from '../lib/api';
import { useToast } from '../hooks/use-toast';
import AdDisplay from './AdDisplay';
import DocumentChat from './DocumentChat';

const DocumentDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);
  const [showDownloadAd, setShowDownloadAd] = useState(false);

  useEffect(() => {
    loadDocument();
  }, [id]);

  const loadDocument = async () => {
    try {
      const documentData = await documentsAPI.getById(id);
      setDocument(documentData);
    } catch (error) {
      console.error('Error loading document:', error);
      if (error.response?.status === 404) {
        setError('Document non trouvé');
      } else {
        setError('Erreur lors du chargement du document');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      // Show ad trigger
      setShowDownloadAd(false); // Reset
      setTimeout(() => setShowDownloadAd(true), 100);

      // Open download link in new tab
      window.open(documentsAPI.download(id), '_blank');

      // Update download count locally
      setDocument(prev => ({
        ...prev,
        download_count: prev.download_count + 1
      }));
    } catch (error) {
      console.error('Download error:', error);
    } finally {
      setDownloading(false);
    }
  };

  const handlePreview = () => {
    window.open(documentsAPI.preview(id), '_blank');
  };

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast({
        title: "Lien copié !",
        description: "Le lien du document a été copié dans votre presse-papier.",
      });

      // Also try native share if available
      if (navigator.share) {
        await navigator.share({
          title: document.title,
          text: document.description,
          url: window.location.href,
        });
      }
    } catch (error) {
      console.log('Error sharing:', error);
      toast({
        title: "Erreur",
        description: "Impossible de copier le lien.",
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center space-x-4">
          <Skeleton className="h-10 w-10" />
          <Skeleton className="h-8 w-32" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <Skeleton className="h-8 w-3/4" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </CardHeader>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent className="space-y-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <div className="mt-6 text-center">
          <Button onClick={() => navigate('/documents')}>
            Retour aux documents
          </Button>
        </div>
      </div>
    );
  }

  if (!document) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {showDownloadAd && <AdDisplay triggerAction="on_download" />}
      {/* Back Button */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <Button variant="ghost" onClick={() => navigate('/documents')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour aux documents
        </Button>

        <div className="flex items-center gap-2 flex-wrap">
          <Button onClick={handlePreview} variant="outline">
            <ExternalLink className="h-4 w-4 mr-2" />
            Plein écran
          </Button>
          <Button onClick={handleShare} variant="outline">
            <Share2 className="h-4 w-4 mr-2" />
            Partager
          </Button>
          <Button onClick={handleDownload} disabled={downloading}>
            <Download className="h-4 w-4 mr-2" />
            {downloading ? 'Téléchargement...' : 'Télécharger'}
          </Button>
        </div>
      </div>

      {/* Header */}
      <Card>
        <CardHeader className="space-y-3">
          <div className="space-y-1">
            <CardTitle className="text-2xl">{document.title}</CardTitle>
            <CardDescription className="text-base">
              {document.description || 'Aucune description disponible'}
            </CardDescription>
          </div>

          <div className="flex items-center flex-wrap gap-2">
            <Badge variant="secondary" className="text-sm">
              {document.course?.name}
            </Badge>
            {document.study_level && (
              <Badge variant="outline" className="text-sm">
                {document.study_level}{document.study_sublevel ? ` • ${document.study_sublevel}` : ''}
              </Badge>
            )}
            {Array.isArray(document.tags) && document.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-sm">
                #{tag}
              </Badge>
            ))}
            <span className="text-sm text-muted-foreground flex items-center ml-1">
              <FileText className="h-4 w-4 mr-1" />
              {document.file_size_mb} MB
            </span>
            <span className="text-sm text-muted-foreground flex items-center">
              <Download className="h-4 w-4 mr-1" />
              {document.download_count} téléchargement{document.download_count > 1 ? 's' : ''}
            </span>
          </div>
        </CardHeader>
      </Card>

      {/* Mobile: Tabs (Document / IA) */}
      <div className="lg:hidden">
        <Tabs defaultValue="doc">
          <TabsList className="w-full">
            <TabsTrigger value="doc" className="flex-1">
              Document
            </TabsTrigger>
            <TabsTrigger value="ai" className="flex-1">
              Assistant IA
            </TabsTrigger>
          </TabsList>

          <TabsContent value="doc" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Eye className="h-5 w-5 mr-2" />
                  Prévisualisation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="aspect-[3/4] bg-muted rounded-lg overflow-hidden">
                  <iframe
                    src={documentsAPI.preview(id)}
                    className="w-full h-full"
                    title={`Prévisualisation de ${document.title}`}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Informations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-1">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <User className="h-4 w-4 mr-2" />
                    Partagé par
                  </div>
                  <p className="font-medium">
                    {document.uploaded_by?.first_name} {document.uploaded_by?.last_name}
                    <span className="text-muted-foreground ml-1">
                      (@{document.uploaded_by?.username})
                    </span>
                  </p>
                </div>

                <Separator />

                <div className="space-y-1">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4 mr-2" />
                    Publication
                  </div>
                  <p className="text-sm">{formatDate(document.created_at)}</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai" className="space-y-6">
            <DocumentChat
              documentId={id}
              documentTitle={document.title}
              className="min-h-[70vh]"
            />
          </TabsContent>
        </Tabs>
      </div>

      {/* Desktop: Split view (Preview + IA) */}
      <div className="hidden lg:grid grid-cols-12 gap-6">
        <div className="col-span-7 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Eye className="h-5 w-5 mr-2" />
                Document
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[calc(100vh-320px)] min-h-[520px] bg-muted rounded-lg overflow-hidden">
                <iframe
                  src={documentsAPI.preview(id)}
                  className="w-full h-full"
                  title={`Prévisualisation de ${document.title}`}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Informations</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-3 gap-4">
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground flex items-center">
                  <User className="h-4 w-4 mr-2" />
                  Auteur
                </div>
                <div className="font-medium">
                  {document.uploaded_by?.first_name} {document.uploaded_by?.last_name}
                </div>
                <div className="text-sm text-muted-foreground">
                  @{document.uploaded_by?.username}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground flex items-center">
                  <Calendar className="h-4 w-4 mr-2" />
                  Publication
                </div>
                <div className="text-sm">{formatDate(document.created_at)}</div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground flex items-center">
                  <Download className="h-4 w-4 mr-2" />
                  Téléchargements
                </div>
                <div className="text-sm">{document.download_count}</div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="col-span-5">
          <div className="sticky top-6 h-[calc(100vh-180px)]">
            <DocumentChat
              documentId={id}
              documentTitle={document.title}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentDetailPage;
