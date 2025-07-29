/**
 * Document Detail Page Component for PDF Course Sharing Platform
 * Developed by Marino ATOHOUN
 */

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
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
import { useAuth } from '../hooks/useAuth';

const DocumentDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

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
    if (navigator.share) {
      try {
        await navigator.share({
          title: document.title,
          text: document.description,
          url: window.location.href,
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      // You could show a toast here
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

  const isOwner = isAuthenticated && user?.user?.id === document.uploaded_by?.id;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back Button */}
      <Button variant="ghost" onClick={() => navigate('/documents')} className="mb-4">
        <ArrowLeft className="h-4 w-4 mr-2" />
        Retour aux documents
      </Button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-2 flex-1">
                  <CardTitle className="text-2xl">{document.title}</CardTitle>
                  <CardDescription className="text-base">
                    {document.description || 'Aucune description disponible'}
                  </CardDescription>
                </div>
              </div>
              
              <div className="flex items-center space-x-4 flex-wrap gap-2">
                <Badge variant="secondary" className="text-sm">
                  {document.course?.name}
                </Badge>
                <span className="text-sm text-muted-foreground flex items-center">
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

          {/* PDF Preview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Eye className="h-5 w-5 mr-2" />
                Prévisualisation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="aspect-[3/4] bg-muted rounded-lg flex items-center justify-center">
                <iframe
                  src={documentsAPI.preview(id)}
                  className="w-full h-full rounded-lg"
                  title={`Prévisualisation de ${document.title}`}
                />
              </div>
              <div className="mt-4 text-center">
                <Button onClick={handlePreview} variant="outline">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Ouvrir en plein écran
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                onClick={handleDownload} 
                disabled={downloading}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                {downloading ? 'Téléchargement...' : 'Télécharger'}
              </Button>
              
              <Button 
                onClick={handlePreview} 
                variant="outline" 
                className="w-full"
              >
                <Eye className="h-4 w-4 mr-2" />
                Prévisualiser
              </Button>
              
              <Button 
                onClick={handleShare} 
                variant="outline" 
                className="w-full"
              >
                <Share2 className="h-4 w-4 mr-2" />
                Partager
              </Button>
            </CardContent>
          </Card>

          {/* Document Info */}
          <Card>
            <CardHeader>
              <CardTitle>Informations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <User className="h-4 w-4 mr-2 text-muted-foreground" />
                  <span className="text-muted-foreground">Partagé par:</span>
                </div>
                <p className="font-medium">
                  {document.uploaded_by?.first_name} {document.uploaded_by?.last_name}
                  <span className="text-muted-foreground ml-1">
                    (@{document.uploaded_by?.username})
                  </span>
                </p>
              </div>

              <Separator />

              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                  <span className="text-muted-foreground">Date de publication:</span>
                </div>
                <p className="text-sm">{formatDate(document.created_at)}</p>
              </div>

              <Separator />

              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <FileText className="h-4 w-4 mr-2 text-muted-foreground" />
                  <span className="text-muted-foreground">Taille du fichier:</span>
                </div>
                <p className="text-sm">{document.file_size_mb} MB</p>
              </div>

              <Separator />

              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <Download className="h-4 w-4 mr-2 text-muted-foreground" />
                  <span className="text-muted-foreground">Téléchargements:</span>
                </div>
                <p className="text-sm">{document.download_count}</p>
              </div>
            </CardContent>
          </Card>

          {/* Related Documents */}
          <Card>
            <CardHeader>
              <CardTitle>Documents similaires</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center text-muted-foreground">
                <p className="text-sm">Fonctionnalité à venir</p>
                <Button variant="outline" size="sm" className="mt-2" asChild>
                  <Link to={`/documents?course=${document.course?.id}`}>
                    Voir tous les cours de {document.course?.name}
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DocumentDetailPage;

