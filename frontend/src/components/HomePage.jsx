/**
 * Home Page Component for PDF Course Sharing Platform
 * Developed by Marino ATOHOUN
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BookOpen, Users, Download, FileText, ArrowRight, Upload, Search } from 'lucide-react';
import { statsAPI, documentsAPI, coursesAPI } from '../lib/api';
import { useAuth } from '../hooks/useAuth';

const HomePage = () => {
  const { isAuthenticated } = useAuth();
  const [stats, setStats] = useState({});
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsData, documentsData, coursesData] = await Promise.all([
        statsAPI.getStats(),
        documentsAPI.getAll({ limit: 6 }),
        coursesAPI.getAll()
      ]);
      
      setStats(statsData);
      setRecentDocuments(documentsData.slice(0, 6));
      setCourses(coursesData.slice(0, 8));
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, description }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center space-y-6">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
            Partagez et découvrez des
            <span className="text-primary"> cours PDF</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            EduShare est une plateforme gratuite de partage de documents PDF éducatifs. 
            Partagez vos cours et accédez à une bibliothèque de ressources pédagogiques.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" asChild>
            <Link to="/documents" className="flex items-center space-x-2">
              <Search className="h-5 w-5" />
              <span>Parcourir les cours</span>
            </Link>
          </Button>
          {isAuthenticated ? (
            <Button size="lg" variant="outline" asChild>
              <Link to="/upload" className="flex items-center space-x-2">
                <Upload className="h-5 w-5" />
                <span>Partager un cours</span>
              </Link>
            </Button>
          ) : (
            <Button size="lg" variant="outline" asChild>
              <Link to="/register" className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Rejoindre la communauté</span>
              </Link>
            </Button>
          )}
        </div>
      </section>

      {/* Statistics */}
      {!loading && (
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard
            icon={FileText}
            title="Documents partagés"
            value={stats.total_documents || 0}
            description="Cours PDF disponibles"
          />
          <StatCard
            icon={BookOpen}
            title="Domaines de cours"
            value={stats.total_courses || 0}
            description="Différentes matières"
          />
          <StatCard
            icon={Users}
            title="Utilisateurs"
            value={stats.total_users || 0}
            description="Membres de la communauté"
          />
          <StatCard
            icon={Download}
            title="Téléchargements"
            value={stats.total_downloads || 0}
            description="Documents téléchargés"
          />
        </section>
      )}

      {/* Features */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold">Pourquoi choisir EduShare ?</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Une plateforme simple et efficace pour partager et accéder à des ressources éducatives
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <Upload className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Partage facile</CardTitle>
              <CardDescription>
                Uploadez vos cours PDF en quelques clics et partagez-les avec la communauté
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card>
            <CardHeader>
              <Search className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Recherche avancée</CardTitle>
              <CardDescription>
                Trouvez rapidement les cours qui vous intéressent grâce à notre système de recherche
              </CardDescription>
            </CardHeader>
          </Card>
          
          <Card>
            <CardHeader>
              <FileText className="h-8 w-8 text-primary mb-2" />
              <CardTitle>Prévisualisation</CardTitle>
              <CardDescription>
                Prévisualisez les documents avant de les télécharger pour gagner du temps
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* Recent Documents */}
      {recentDocuments.length > 0 && (
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold">Documents récents</h2>
            <Button variant="outline" asChild>
              <Link to="/documents" className="flex items-center space-x-2">
                <span>Voir tous</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentDocuments.map((doc) => (
              <Card key={doc.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg line-clamp-2">{doc.title}</CardTitle>
                      <CardDescription className="line-clamp-2">
                        {doc.description || 'Aucune description disponible'}
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary">{doc.course_domain}</Badge>
                    <span className="text-sm text-muted-foreground">
                      {doc.file_size_mb} MB
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      Par {doc.uploaded_by_username}
                    </span>
                    <Button size="sm" asChild>
                      <Link to={`/documents/${doc.id}`}>Voir</Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* Courses Categories */}
      {courses.length > 0 && (
        <section className="space-y-6">
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-bold">Domaines de cours</h2>
            <p className="text-muted-foreground">
              Explorez nos différentes catégories de cours
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {courses.map((course) => (
              <Card key={course.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader className="text-center">
                  <BookOpen className="h-8 w-8 text-primary mx-auto mb-2" />
                  <CardTitle className="text-lg">{course.name}</CardTitle>
                  <CardDescription>
                    {course.documents_count} document{course.documents_count > 1 ? 's' : ''}
                  </CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* Call to Action */}
      <section className="text-center space-y-6 bg-muted/50 rounded-lg p-8">
        <h2 className="text-3xl font-bold">Prêt à commencer ?</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Rejoignez notre communauté d'étudiants et d'enseignants qui partagent leurs connaissances
        </p>
        {!isAuthenticated && (
          <Button size="lg" asChild>
            <Link to="/register">Créer un compte gratuit</Link>
          </Button>
        )}
      </section>
    </div>
  );
};

export default HomePage;

